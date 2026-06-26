def report_error(
    error_def: ErrorDefinition,
    original_exception: Exception,
    context: dict,
    *,
    metadata: dict | None = None,
    message: str | None = None,
    dispatcher_config: DispatcherConfig | None = None,
    handler: Handler | None = None,                     # single-use override for this error’s action
    handler_overrides: Dict[RecommendedAction, Handler] | None = None,  # map of overrides
    extra: Dict[str, Any] | None = None,                # forwarded to dispatch_action.extra
) -> ActionOutcome | None:


DEFAULT_HANDLERS: Dict[RecommendedAction, Handler] = {
    RecommendedAction.LOG_ONLY: _noop,
    RecommendedAction.PROMPT_USER: _prompt_user_gui,
    RecommendedAction.RETRY_OPERATION: _retry_op,
    RecommendedAction.SKIP_STEP: _skip_step,
    RecommendedAction.RELOAD_PLAN: _reload_plan,
    RecommendedAction.ALERT_PHYSICIST: _alert_physicist,
    RecommendedAction.SAVE_AND_EXIT: _save_and_exit,
    RecommendedAction.ABORT_SCRIPT: _abort_script
}

def _noop(ctx: DispatchContext) -> ActionOutcome:
    return ActionOutcome(action=ctx.action)
