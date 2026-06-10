import logging
from enum import Enum, auto

logger = logging.getLogger(__name__)


class State(Enum):
    """All possible states of the bot's finite state machine."""

    IDLE = auto()
    CONNECTING = auto()
    HOME_VILLAGE = auto()
    FARMING = auto()
    SEARCHING_ATTACK = auto()
    ATTACKING = auto()
    WAITING_TROOPS = auto()
    ERROR = auto()
    STOPPING = auto()


class StateMachine:
    """Simple finite state machine for the bot.

    Example:
        sm = StateMachine()
        sm.transition(State.CONNECTING)
        sm.transition(State.HOME_VILLAGE)
    """

    # Allowed transitions: state -> set of reachable next states
    _TRANSITIONS: dict[State, set[State]] = {
        State.IDLE: {State.CONNECTING},
        State.CONNECTING: {State.HOME_VILLAGE, State.ERROR},
        State.HOME_VILLAGE: {State.FARMING, State.SEARCHING_ATTACK, State.ERROR, State.STOPPING},
        State.FARMING: {State.HOME_VILLAGE, State.ERROR, State.STOPPING},
        State.SEARCHING_ATTACK: {State.ATTACKING, State.HOME_VILLAGE, State.ERROR, State.STOPPING},
        State.ATTACKING: {State.WAITING_TROOPS, State.HOME_VILLAGE, State.ERROR},
        State.WAITING_TROOPS: {State.HOME_VILLAGE, State.SEARCHING_ATTACK, State.ERROR},
        State.ERROR: {State.IDLE, State.STOPPING},
        State.STOPPING: set(),
    }

    def __init__(self) -> None:
        self.current: State = State.IDLE
        self._history: list[State] = [State.IDLE]

    def transition(self, next_state: State) -> None:
        """Move to a new state, validating the transition first.

        Args:
            next_state: Target state.

        Raises:
            ValueError: if the transition is not allowed.
        """
        allowed = self._TRANSITIONS.get(self.current, set())
        if next_state not in allowed:
            raise ValueError(
                f"Invalid transition: {self.current.name} -> {next_state.name}"
            )
        logger.info("State: %s -> %s", self.current.name, next_state.name)
        self.current = next_state
        self._history.append(next_state)

    def is_running(self) -> bool:
        """Return True while the bot is in an active (non-terminal) state."""
        return self.current not in (State.IDLE, State.STOPPING, State.ERROR)
