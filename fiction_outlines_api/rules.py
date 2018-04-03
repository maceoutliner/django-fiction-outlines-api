'''
Rules definitions for api. We just import in the default rules from fiction_outlines.
'''
import rules
from fiction_outlines.rules import *  # noqa: F401, F403


@rules.predicate
def is_auth_user(user):
    return user.is_authenticated


rules.add_perm('fiction_outlines_api.valid_user', is_auth_user)
