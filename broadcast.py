"""Live broadcast-booth commentary.

Turns each play-by-play event into an excited, conversational announcer call
(the way a TV broadcast talks), using live player stats for color. This is a
separate feed from the play-by-play -- it never changes the sim.

Placeholders available in a line (a line is only used when every key it
needs is known for the current event):
  {p} player   {d} defender   {passer} assisting passer   {team}/{opp} teams
  {pts} {fgm} {fga} {tpm} {tpa} {reb} {ast} {pf}   the player's game totals
  {lead} margin of the leading team   {run} the team's current run   {score} "89-96"
"""
import random
import re
import string
from collections import deque


def _keys(line: str) -> frozenset:
    return frozenset(name for _, name, _, _ in string.Formatter().parse(line) if name)


MAKE_THREE = [
    "Bang! {p} from downtown.",
    "{p} lets it fly, and it is good.",
    "Oh, that's cold-blooded from {p}.",
    "Nothing but the bottom of the net. {p} from deep.",
    "{p} does not hesitate, and the three drops.",
    "From way out there... got it! {p}.",
    "That's a long one, and {p} buries it.",
    "Wow. {p} pulls up and splashes the three.",
    "{p} rises up, and it's pure.",
    "Right in the pocket and right through. {p} from three.",
    "{p} with the step-back, and he cashes it.",
    "Look at the confidence. {p} drills the three.",
    "The defense had no answer for that one. {p} with the triple.",
    "He's feeling it now. {p} knocks down another from deep.",
    "{p} catches, and there is no thinking about it. Three.",
    "Quick release, and {p} is money from the perimeter.",
    "Oh, that's a beautiful look. {p} hits the three.",
    "{p} from the logo area, and it goes in!",
    "That ball was never leaving the net. {p} from three.",
    "{p} steps into it, and the building comes alive.",
    "Straight through the nylon. {p} with the three-pointer.",
    "{p} drains it, and {team} are rolling.",
    "He's got range for days. {p} makes the three.",
    "That's the shot you want {p} taking. Good!",
    "{p} off the dribble, from deep, and it's down.",
    "Splash. {p} makes it look easy.",
    "{p} with the corner three, right in front of the bench.",
    "Hand in his face, and {p} still knocks it down.",
    "{p} on the kickout, no hesitation, and it's good.",
    "That's three more for {p}, and {team} extend the margin.",
]

MAKE_MID = [
    "{p} with the pull-up, and it's good.",
    "Smooth. {p} elevates over the top of {d} and hits the jumper.",
    "{p} gets to the elbow and knocks it down.",
    "That is a tough shot, and {p} makes it look routine.",
    "Midrange money for {p}.",
    "{p} stops on a dime and fires. Good!",
    "Oh, what a jumper from {p}.",
    "Right in the soft spot, and {p} cashes it.",
    "Nobody is going to stop that shot. {p} with the midrange.",
    "{p} rises over the defender and drains it.",
    "{p} fades away, and it's in!",
    "Pure touch from {p}.",
    "He just gets to his spot and does it. {p} with the jumper.",
    "That's the old reliable. {p} hits the elbow jumper.",
    "{p} spins, balances, and knocks down the shot.",
    "{p} with a little hesitation and the pull-up goes.",
    "Textbook. {p} from the free throw line, and it's good.",
    "That's the way you get a bucket against a set defense. {p}.",
    "{p} sizes up {d}, then rises into a jumper. Beautiful.",
    "The defense played it well, and {p} hit it anyway.",
    "Sweet release from {p}. Money.",
    "{p} off one dribble, up, and it goes.",
    "Easy as that. {p} with the midrange shot.",
    "{p} turns the corner, stops, and drains it.",
]

MAKE_PAINT = [
    "{p} gets to the rim and finishes.",
    "Oh, what a move by {p}. Lays it in.",
    "{p} somehow gets that one to go. Beautiful finish.",
    "Look at the body control. {p} scoops it in.",
    "{p} with the crafty finish at the rim.",
    "He just glided through the defense. {p} with the layup.",
    "{p} spins, avoids the contact, and puts it in off the glass.",
    "{p} goes right through the middle and scores.",
    "Too quick, too strong. {p} finishes inside.",
    "{p} with the reverse layup, and it falls.",
    "Where did he come from? {p} gets it up and in.",
    "That's the kind of finish you cannot teach. {p}.",
    "{p} hangs in the air, hangs some more, and lays it in.",
    "Floater from {p}, and it drops.",
    "{p} drives, takes the bump, and scores.",
    "{p} gets it done in traffic. Beautiful.",
    "A little English off the glass and {p} is on the board again.",
    "Nobody was going to stop that. {p} inside.",
    "{p} with the up-and-under, and it's good.",
    "He just walks the defense down and finishes. {p}.",
    "{p} puts it in with the left hand.",
    "Strong move from {p}, and he takes it right to the cup.",
    "{p} around {d} like he was standing still, and it's two.",
    "{p} powers through the contact and scores.",
    "Quick first step, and {p} is at the rim in a flash.",
    "{p} in the post, the turnaround, and it falls.",
    "That was the hook from {p}. Nobody guards that.",
    "Soft touch from {p} on the finish.",
    "{p} spins baseline and lays it in. Wow.",
    "{p} with the strong finish. Get a hand in his face and he still scores.",
]

MAKE_DUNK = [
    "Oh, my goodness! {p} with the slam!",
    "{p} takes off, and he throws it down!",
    "Wow. {p} rocks the rim.",
    "Are you kidding me? {p} with the dunk!",
    "{p} rises and detonates on {d}!",
    "That is a poster! {p}!",
    "{p} catches it above the rim and finishes with authority.",
    "Nobody home at the rim, and {p} flushes it.",
    "{p} puts it down with two hands, and the crowd is on its feet.",
    "What a lob, and what a finish from {p}.",
    "{p} off the glass, and he slams it home.",
    "That is a thunderous dunk from {p}.",
    "{p} attacks the rim like he's angry at it.",
    "Right over the top of the defender. {p} with the jam.",
    "{p} in transition, up, and throws it down!",
    "Oh, he's going to remember that one. {p} dunks it!",
    "{p} with the one-hand tomahawk!",
    "The rim is still shaking. {p} with the slam.",
    "{p} gets the lob and finishes above everybody.",
    "Highlight reel stuff from {p}.",
    "{p} elevates, and that is two with a statement.",
    "Wow, look at the hang time on {p}.",
    "{p} puts {d} on a poster.",
    "That one was never in doubt. {p} dunks it.",
]

MAKE_AND_ONE = [
    "And the foul! {p} gets the and-one!",
    "{p} scores through the contact, and he'll go to the line!",
    "Oh, he's going to get the three-point play. {p}!",
    "Bucket and the foul on {d}. {p} has a free throw coming.",
    "{p} finishes through the whistle. And one!",
    "Strong. {p} takes the hit, scores, and the whistle blows.",
    "That's a four-point swing. {p} scores and draws the foul.",
    "{p} with the finish, and now the chance for a bonus point.",
    "Contact, bucket, whistle. {p} will shoot one.",
    "{p} will not be denied. And one.",
    "Can he make the free throw? {p} will find out in a moment.",
    "{d} gets the foul, and {p} gets the points.",
    "That is a big play. {p} converts the three-point play opportunity.",
    "{p} powers it in, and there's the foul.",
]

MAKE_ASSISTED = [
    "Beautiful feed from {passer}, and {p} finishes.",
    "{passer} to {p}, and that's a bucket.",
    "Great vision from {passer}. {p} makes the most of it.",
    "{passer} finds {p}, and he knocks it down.",
    "What a pass from {passer}. {p} just had to finish.",
    "Ball movement at its best. {passer} sets up {p}.",
    "{passer} with the dime, and {p} cashes it.",
    "Oh, that's a nice read from {passer}. {p} scores.",
    "{p} was waiting, and {passer} delivered.",
    "{passer} threads the needle to {p}. Two points.",
    "The extra pass from {passer} finds {p}, and he doesn't miss.",
    "That's the right play. {passer} to {p}, and it's good.",
    "{passer} draws the help and kicks it to {p}. Bucket.",
    "{passer} to {p}. Easy as that.",
    "Look at the touch pass from {passer}. {p} finishes.",
    "{passer} is running the show, and {p} is the beneficiary.",
    "{p} off the feed from {passer}, and it's good.",
    "Crisp, quick, and clean. {passer} to {p}.",
    "{passer} finds the open man, {p}, and that's two more for {team}.",
    "Unselfish play from {passer}, and {p} rewards him.",
    "A beautiful, beautiful pass from {passer}.",
    "{passer} with the no-look to {p}, and the defense is lost.",
    "{p} slides into the open space, and {passer} finds him.",
    "That's an assist for {passer}, and a bucket for {p}.",
]

MAKE_STAT = [
    "{p} now {fgm} of {fga} from the field.",
    "That's {pts} points for {p}.",
    "He's got {pts}. {p} is feeling it.",
    "{p} is up to {pts}, and {team} are feeding him.",
    "{p} has {pts} points on {fgm} of {fga} shooting.",
    "{pts} points for {p}, and he's not slowing down.",
    "{p} is {fgm} for {fga} and he's rolling.",
    "{p} is {tpm} for {tpa} from three, and that was a big one.",
    "{p} has been the best player on the floor tonight.",
    "{p} is putting on a show with {pts} points.",
    "That's {pts} for {p}. Somebody has to do something about him.",
    "{p} just keeps scoring. {pts} points now.",
    "The scouting report said stop {p}, and here he is with {pts}.",
    "{fgm} of {fga} for {p}. That's efficient.",
    "{p} is {tpm} of {tpa} from deep, and he wants more.",
    "You can't leave {p} alone, and he's got {pts} to prove it.",
    "{p} is carrying {team} right now.",
    "{p} with {pts}, and he's making it look easy.",
    "The crowd knows it and the defense knows it. {p} has {pts}.",
    "{p} owns this stretch of the game.",
    "Check the box score: {pts} points for {p}.",
    "{p} adds to a big night. {pts} points.",
]

HYPE = [
    "Nobody in this game can do the special things with the ball like {p}.",
    "That's vintage {p}.",
    "{p} is in his bag right now.",
    "{p} against the world.",
    "That's why they call him a star. {p}.",
    "Wow. Just wow.",
    "You have to see it to believe it.",
    "That was filthy.",
    "{p} is a magician with the basketball.",
    "I wouldn't want to guard {p} right now.",
    "Spectacular. Absolutely spectacular.",
    "{p} makes the difficult look routine.",
    "That's a showstopper from {p}.",
    "Just a master at work. {p}.",
    "That is why you come to the game. {p}.",
    "He is the best in the business at that. {p}.",
    "{p} is cooking.",
    "You can't scheme for that. {p} is just better.",
    "Oh, boy. {p} has some talent.",
    "That was a whoa-whoa move from {p}.",
]

RUN_LINES = [
    "{team} are on a {run}-0 run, and the other bench is on its feet.",
    "{run} straight points for {team}. The momentum has shifted.",
    "{team} have strung together {run} in a row, and the building is loud.",
    "It's a {run}-0 run for {team}. Somebody has to stop the bleeding.",
    "{team} are rolling now, {run} unanswered.",
    "The game is turning, {team} with {run} in a row.",
    "{opp} cannot buy a stop. {team} with {run} straight.",
    "{team} have ripped off {run} points, and the lead is {lead}.",
]

LEAD_LINES = [
    "{team} take the lead!",
    "And {team} are in front.",
    "We have a new leader. {team} go ahead.",
    "{team} grab the lead, and that was a big bucket.",
    "That puts {team} on top, and the crowd goes crazy.",
    "{team} go in front, and {opp} have to respond.",
    "A lead change, and {team} are the ones on top.",
    "{team} ahead by {lead}, after that one.",
]

TIE_LINES = [
    "We are tied at {score}.",
    "All square. {score}.",
    "{team} pull even. It's a tie game.",
    "That ties it up, {score}.",
    "Tie game, and everyone in here knows it.",
]

LEAD_STATE = [
    "{team} lead by {lead}, and they look comfortable.",
    "{lead} is the margin now, {team} in control.",
    "{team} extend it to {lead}.",
    "{opp} down {lead}, and they need a stop.",
    "{team} push the lead up to {lead}.",
    "That's a {lead}-point game now.",
]

MISS_LINES = [
    "{p} misses it.",
    "Oh, that one rattles out. {p}.",
    "{p} can't get that one to go.",
    "No good. {p} comes up short.",
    "Off the mark for {p}.",
    "{p} rims it out.",
    "That was a good look, but it doesn't fall for {p}.",
    "Front rim. {p} wanted that one back.",
    "Good defense from {d}. {p} misses.",
    "{p} had a decent look, and it rattles in and out.",
    "Just a hair off. {p} misses.",
    "{d} makes it tough, and {p} can't convert.",
    "{p} doesn't get a good bounce on that one.",
    "That's a miss, and the rebound is up for grabs.",
    "It looked good coming off his hand, but {p} misses.",
    "Not a great shot, and it shows. {p} misses.",
    "{p} tries to force it, and it won't go.",
    "{p} was contested, and it falls short.",
    "Short. Just short. {p}.",
    "{p} goes up strong, and it rolls off.",
    "Well-defended by {d}. {p} misses.",
    "Back iron. {p} can't connect.",
    "The shot is off. {p} will want to forget that one.",
    "Missed it. {p} can't buy one right now.",
    "{p} fires, and it doesn't fall.",
    "{p} tried to get it up there, and the rim says no.",
    "{d} with a hand up, and {p} can't finish.",
    "No luck for {p} on that possession.",
]

MISS_COLD = [
    "{p} is {fgm} of {fga} tonight, and that one wasn't close.",
    "{p} is struggling. {fgm} for {fga} from the field.",
    "That's another miss for {p}, who is {tpm} of {tpa} from three.",
    "{p} is looking for a rhythm and can't find it.",
    "{p} has been ice cold, {fgm} of {fga}.",
    "{p} needs one to go in the worst way.",
    "{fgm} for {fga} for {p}. He has to find a way to get going.",
    "{team} can't afford many more of those from {p}.",
    "That's the third one in a row for {p}, and the cold streak continues.",
    "{p} is fighting it tonight.",
    "{p} keeps shooting, and the bucket keeps saying no.",
    "{p} is {tpm} of {tpa} from deep. Might be time to attack the rim.",
]

FT_MAKE = [
    "{p} makes the free throw.",
    "Good at the line. {p}.",
    "{p} knocks it down from the stripe.",
    "Nothing but net from {p} at the line.",
    "{p} is cool, calm, and collected at the line.",
    "{p} sinks it. That's automatic.",
    "Both teams know what that free throw means. {p} makes it.",
    "{p} steps up, and it falls.",
    "{p} with the clean stroke from the line.",
    "The free throw is good. {p} adds a point.",
    "{p} converts at the line.",
    "That's money. {p} from the line.",
    "{p} doesn't flinch. Good.",
    "{p} drops it in.",
]

FT_MISS = [
    "{p} misses the free throw.",
    "Oh, it rims out for {p} at the line.",
    "Short. {p} misses from the stripe.",
    "A rare miss at the line for {p}.",
    "{p} can't convert at the line.",
    "That free throw is no good, and it matters.",
    "{p} wanted that one, but it rolls out.",
    "{p} leaves it short.",
    "The pressure shows. {p} misses.",
    "Back rim. {p} misses the free throw.",
    "That's a costly miss from {p}.",
    "{p} doesn't get the roll on that free throw.",
]

BLOCK_LINES = [
    "Rejected! {d} sends it back!",
    "Not in my house! {d} with the block!",
    "{d} swats it away!",
    "What a block by {d}!",
    "{d} meets {p} at the rim and says no.",
    "{d} with the huge rejection!",
    "{p} goes up, and {d} sends it to the third row.",
    "Get that out of here! {d} with the stuff!",
    "Great timing from {d}. Block.",
    "{d} erases the shot at the rim.",
    "{d} comes out of nowhere and blocks it!",
    "{p} thought he had it, but {d} had other ideas.",
    "That's the defensive play of the night so far. {d} with the block.",
    "{d} protects the rim, and {p} finds out the hard way.",
    "Oh, and {d} is not done. Another block!",
    "{d} stuffs {p} at the summit.",
    "{d} got all ball on that one.",
    "{p} drives in, and {d} sends it back!",
    "Vicious block from {d}.",
    "{d} with a sensational rejection.",
    "And that is the block! {d}!",
    "{d} sends {p}'s shot into the stands.",
]

STEAL_LINES = [
    "{p} with the steal!",
    "{p} takes it away, and {team} are off to the races.",
    "Pickpocket! {p} strips the ball.",
    "{p} reads the pass and jumps the lane!",
    "Great hands from {p}. Steal.",
    "{p} comes up with it, and he is gone!",
    "That's a turnover, and {p} is the thief.",
    "{p} with the deflection and the steal.",
    "Careless with the ball, and {p} makes them pay.",
    "{p} anticipated that one perfectly.",
    "Active hands from {p}. Steal.",
    "{p} picks his pocket!",
    "Oh, that's a gift, and {p} accepts.",
    "{p} jumps the passing lane, and {team} have the ball.",
    "The ball is stripped by {p}, and they go the other way!",
    "{p} is all over the place defensively. Another steal.",
    "{p} with a clean take-away.",
    "Nice defensive effort by {p}. Steal.",
    "{p} reads it like a book.",
    "Bad pass, and {p} takes full advantage.",
    "{p} comes away with the ball and starts the break.",
    "{p} with the strip, and the possession flips.",
]

FOUL_LINES = [
    "Whistle on {p}. That's a foul.",
    "{p} is called for the foul.",
    "The officials get {p} for the contact.",
    "{p} reached, and the whistle blows.",
    "That's a foul on {p}, and {opp} will shoot.",
    "{p} was a step late, and the ref saw it.",
    "Contact from {p}, and the whistle blows.",
    "That's going to be a foul on {p}.",
    "The referee gets {p} for the hand-check.",
    "{p} can't afford that one.",
    "{p} hacks him on the way up. Foul.",
    "Whistle! {p} with the foul.",
    "{p} bumps him, and that is a call.",
    "{p} grabbed him, and the ref saw it.",
    "That's a tough one for {p}, but the whistle is blown.",
    "Foul on {p}. He's frustrated.",
    "{p} puts his hands on him, and that's a foul.",
    "Pretty clear contact from {p}.",
    "{p} is called for the foul, and {team} are in a bind.",
    "Heavy contact. Foul on {p}.",
]

FOUL_TROUBLE = [
    "That is {pf} fouls on {p}, and he's going to have to be careful.",
    "{p} picks up his {pf}th foul. Trouble for {team}.",
    "{p} has {pf} fouls. The coach has some decisions to make.",
    "{p} is in foul trouble with {pf}, and the other team is going to go right at him.",
    "{pf} fouls for {p}. He can't be aggressive anymore.",
    "{team} may have to sit {p} with {pf} fouls.",
]

TURNOVER_LINES = [
    "Turnover! The ball gets away from {p}.",
    "{p} loses the handle, and that's a turnover.",
    "Sloppy possession from {team}. Turnover.",
    "{p} throws it away.",
    "That's a bad pass, and it's a turnover for {team}.",
    "{p} walks, and that's a travel.",
    "A turnover by {p}, and that is a gift for {opp}.",
    "Careless from {p}. Turnover.",
    "{p} can't hold on to it. {opp} will take that.",
    "{p} steps out of bounds, and the ball goes the other way.",
    "That one gets away from {p}. Turnover.",
    "{team} give it away, and {opp} take it the other way.",
    "{p} forces a pass, and it's picked off.",
    "A mistake from {p}, and {opp} get a free possession.",
    "{team} can't take care of the ball.",
    "{p} dribbles into trouble, and that's a turnover.",
]

REBOUND_LINES = [
    "{p} with the rebound.",
    "{p} cleans the glass.",
    "{p} comes away with it in traffic.",
    "Great effort by {p} on the glass.",
    "{p} wins the battle on the boards.",
    "{p} secures the board, and {team} get the ball back.",
    "{p} out-hustles everyone for the rebound.",
    "Nobody boxed out, and {p} takes advantage.",
    "{p} with the strong board.",
    "{p} grabs it, and they'll push it.",
    "A big rebound from {p}.",
    "{p} grabs the miss. {reb} rebounds tonight.",
    "{p} sky-high for the rebound.",
    "{p} corrals it and kicks it out.",
]

TIMEOUT_LINES = [
    "Timeout, {team}.",
    "{team} need to stop the bleeding. Timeout.",
    "{team} call for time, and they have a lot to talk about.",
    "The coach has seen enough. Timeout, {team}.",
    "{team} stop the run with a timeout.",
    "Time out on the floor. {team} regroup.",
    "{team} go to the huddle, and the crowd gets a breather.",
    "Smart timeout from {team}. They needed that.",
    "{team} burn a timeout, and the building settles down.",
    "That's a timeout for {team}, and the momentum is on hold.",
    "{team} pull the plug on that stretch with a timeout.",
    "The bench is up, and {team} are talking things over.",
    "{team} need a plan, and here comes a timeout.",
    "Timeout called. {team} have to settle things down.",
]

SUB_LINES = [
    "{p} checks into the game.",
    "Fresh legs for {team}. {p} is in.",
    "{p} comes in, and {team} look to change the energy.",
    "{p} subs in for {team}.",
    "The coach goes to the bench, and {p} enters.",
    "{p} is on the floor now.",
    "A new look for {team} with {p} in the game.",
    "{p} checks in, and the rotation adjusts.",
    "{p} gets his number called.",
    "Here comes {p} off the bench.",
]

PERIOD_START = [
    "And we are underway. {team} and {opp}, here we go.",
    "New quarter, and the game is still wide open.",
    "Here we go again. The next period gets started.",
    "Back on the floor, and the crowd is ready.",
    "Let's see who comes out with the energy.",
]

PERIOD_END = [
    "That will do it for the quarter.",
    "The buzzer sounds. End of the period.",
    "And that's the end of that quarter. A lot to talk about.",
    "Time to catch our breath. That quarter is in the books.",
    "The horn sounds, and both teams head to the bench.",
]

GAME_END = [
    "And that's the game! What a performance.",
    "It's over. The final buzzer sounds.",
    "That's all she wrote. The game is final.",
]

ALL_POOLS = {
    "make_three": MAKE_THREE, "make_mid": MAKE_MID, "make_paint": MAKE_PAINT,
    "make_dunk": MAKE_DUNK, "and_one": MAKE_AND_ONE, "assisted": MAKE_ASSISTED,
    "stat": MAKE_STAT, "hype": HYPE, "run": RUN_LINES, "lead": LEAD_LINES,
    "tie": TIE_LINES, "lead_state": LEAD_STATE, "miss": MISS_LINES,
    "miss_cold": MISS_COLD, "ft_make": FT_MAKE, "ft_miss": FT_MISS,
    "block": BLOCK_LINES, "steal": STEAL_LINES, "foul": FOUL_LINES,
    "foul_trouble": FOUL_TROUBLE, "turnover": TURNOVER_LINES,
    "rebound": REBOUND_LINES, "timeout": TIMEOUT_LINES, "sub": SUB_LINES,
    "period_start": PERIOD_START, "period_end": PERIOD_END, "game_end": GAME_END,
}

TOTAL_LINES = sum(len(pool) for pool in ALL_POOLS.values())

_POOL_KEYS = {name: [(line, _keys(line)) for line in pool] for name, pool in ALL_POOLS.items()}


class BroadcastBooth:
    """Stateful announcer that turns engine events into broadcast calls.

    Events come from sim_engine.BROADCAST_EVENTS (structured: shot made or
    missed with the shot type and contesting defender, blocks, steals,
    assists, fouls, free throws, timeouts, subs, rebounds, period changes),
    so every call matches what actually happened instead of guessing from
    the play-by-play text.
    """

    SHOT_POOL = {
        "three": "make_three", "mid": "make_mid", "post_fade": "make_mid",
        "dunk": "make_dunk",
    }

    def __init__(self):
        self.recent = deque(maxlen=60)
        self.last_leader = None
        self.last_hype_at = -99
        self.call_count = 0

    def reset(self):
        self.__init__()

    def _pick(self, pool_name: str, ctx: dict) -> str | None:
        have = set(k for k, v in ctx.items() if v not in (None, ""))
        usable = [line for line, need in _POOL_KEYS[pool_name] if need <= have]
        fresh = [line for line in usable if line not in self.recent]
        pool = fresh or usable
        if not pool:
            return None
        line = random.choice(pool)
        self.recent.append(line)
        return line.format(**{k: v for k, v in ctx.items() if not k.startswith("_")})

    @staticmethod
    def _find_team(player, teams):
        for team in teams:
            if team is None:
                continue
            for member in getattr(team, "roster", []):
                if member is player:
                    return team
        return None

    @staticmethod
    def _find_player(name, teams):
        for team in teams:
            if team is None:
                continue
            for member in getattr(team, "roster", []):
                if member.name == name:
                    return member, team
        return None, None

    def _context(self, player, teams) -> dict:
        ctx = {}
        if player is None:
            return ctx
        ctx["p"] = player.name
        team = self._find_team(player, teams)
        if team is not None:
            opp = next((t for t in teams if t is not None and t is not team), None)
            ctx["team"] = getattr(team, "name", None)
            if opp is not None:
                ctx["opp"] = opp.name
                ctx["lead"] = abs(team.score - opp.score)
                ctx["_signed_lead"] = team.score - opp.score
            ctx["run"] = getattr(team, "current_run", 0)
            if teams[0] is not None and teams[1] is not None:
                ctx["score"] = f"{teams[0].score}-{teams[1].score}"
        ctx.update({
            "pts": player.pts, "fgm": player.fgm, "fga": player.fga,
            "tpm": player.tpm, "tpa": player.tpa, "reb": player.reb,
            "ast": player.ast, "pf": player.pf,
        })
        return ctx

    def process(self, events: list, teams) -> list:
        """Return a list of (kind, text) calls for a batch of engine events."""
        calls = []
        skip = set()
        for idx, event in enumerate(events):
            if idx in skip:
                continue
            kind = event.get("kind")
            prev_event = events[idx - 1] if idx > 0 else None
            next_event = events[idx + 1] if idx + 1 < len(events) else None

            if kind == "shot":
                player = event["player"]
                made = event["made"]
                defender = event.get("defender")
                shot_type = event.get("shot_type") or "rim"
                ctx = self._context(player, teams)
                if defender is not None:
                    ctx["d"] = defender.name
                if made:
                    pool = self.SHOT_POOL.get(shot_type, "make_paint")
                    passer = None
                    for neighbor in (prev_event, next_event):
                        if neighbor and neighbor.get("kind") == "assist" and neighbor["passer"] is not player:
                            passer = neighbor["passer"]
                            if neighbor is next_event:
                                skip.add(idx + 1)
                            break
                    if passer is not None:
                        ctx["passer"] = passer.name
                    and_one = bool(
                        next_event and next_event.get("kind") == "foul"
                        and next_event["player"] is not player
                        and self._find_team(next_event["player"], teams) is not self._find_team(player, teams)
                    )
                    if and_one:
                        ctx["d"] = next_event["player"].name
                        skip.add(idx + 1)
                    text = self._make_call(pool, ctx, and_one)
                    if text:
                        calls.append(("make", text))
                else:
                    if next_event and next_event.get("kind") == "block":
                        continue
                    pool = "miss"
                    if ctx.get("fga", 0) >= 6 and ctx.get("fgm", 0) / max(1, ctx["fga"]) < 0.30 and random.random() < 0.45:
                        pool = "miss_cold"
                    text = self._pick(pool, ctx) or self._pick("miss", ctx)
                    if text:
                        calls.append(("miss", text))

            elif kind == "assist":
                continue

            elif kind == "block":
                blocker = event["player"]
                ctx = {k: v for k, v in self._context(blocker, teams).items() if k != "p"}
                ctx["d"] = blocker.name
                if prev_event and prev_event.get("kind") == "shot" and not prev_event["made"]:
                    ctx["p"] = prev_event["player"].name
                text = self._pick("block", ctx)
                if text:
                    calls.append(("block", text))

            elif kind == "steal":
                text = self._pick("steal", self._context(event["player"], teams))
                if text:
                    calls.append(("steal", text))

            elif kind == "turnover":
                text = self._pick("turnover", self._context(event["player"], teams))
                if text:
                    calls.append(("turnover", text))

            elif kind == "foul":
                ctx = self._context(event["player"], teams)
                pool = "foul_trouble" if ctx.get("pf", 0) >= 4 and random.random() < 0.7 else "foul"
                text = self._pick(pool, ctx) or self._pick("foul", ctx)
                if text:
                    calls.append(("foul", text))

            elif kind == "ft":
                text = self._pick("ft_make" if event["made"] else "ft_miss", self._context(event["player"], teams))
                if text:
                    calls.append(("ft", text))

            elif kind == "rebound":
                player, _team = self._find_player(event.get("name"), teams)
                ctx = self._context(player, teams) if player else {"p": event.get("name")}
                text = self._pick("rebound", ctx)
                if text:
                    calls.append(("rebound", text))

            elif kind == "timeout":
                other = next((t.name for t in teams if t is not None and t.name != event.get("team")), None)
                text = self._pick("timeout", {"team": event.get("team"), "opp": other})
                if text:
                    calls.append(("timeout", text))

            elif kind == "sub":
                text = self._pick("sub", {"p": event.get("sub_in"), "team": event.get("team")})
                if text:
                    calls.append(("sub", text))

            elif kind in ("period_start", "period_end", "game_end"):
                named = [t for t in teams if t is not None]
                ctx = {"team": named[0].name, "opp": named[1].name} if len(named) == 2 else {}
                text = self._pick(kind, ctx)
                if text:
                    calls.append((kind, text))
        return calls

    def _make_call(self, pool: str, ctx: dict, and_one: bool = False) -> str:
        parts = []
        if and_one:
            text = self._pick("and_one", ctx)
            if text:
                parts.append(text)
        elif ctx.get("passer") and random.random() < 0.45:
            text = self._pick("assisted", ctx)
            if text:
                parts.append(text)
        if not parts:
            parts.append(self._pick(pool, ctx) or "")

        signed = ctx.get("_signed_lead")
        team = ctx.get("team")
        took_lead = tied = False
        if signed is not None and team:
            leader = team if signed > 0 else ("tie" if signed == 0 else "opp")
            took_lead = leader == team and self.last_leader == "opp"
            tied = leader == "tie" and self.last_leader not in (None, "tie")
            self.last_leader = "tie" if leader == "tie" else (team if leader == team else "opp")
        self.call_count += 1

        extra = None
        if took_lead and random.random() < 0.9:
            extra = self._pick("lead", ctx)
        elif tied and random.random() < 0.9:
            extra = self._pick("tie", ctx)
        elif ctx.get("run", 0) >= 8 and random.random() < 0.6:
            extra = self._pick("run", ctx)
        elif ctx.get("pts", 0) >= 18 and self.call_count - self.last_hype_at > 4 and random.random() < 0.55:
            extra = self._pick("hype" if random.random() < 0.5 else "stat", ctx)
            self.last_hype_at = self.call_count
        elif ctx.get("pts", 0) >= 10 and random.random() < 0.28:
            extra = self._pick("stat", ctx)
        elif signed is not None and abs(signed) >= 10 and random.random() < 0.15:
            extra = self._pick("lead_state", ctx)
        if extra:
            parts.append(extra)
        return " ".join(part for part in parts if part)
