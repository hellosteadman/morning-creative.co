from user_agents import parse


def get_user_agent_info(string, source='user_agents'):
    if (agent := parse(string)) is not None:
        return {
            'browser': agent.browser.family,
            'platform': agent.device.family,
            'device_type': (
                (agent.is_tablet and 'tablet') or
                (agent.is_mobile and 'mobile') or
                (agent.is_pc and 'desktop')
            ) or '',
            'bot': agent.is_bot
        }
