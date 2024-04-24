# this is just used to specify which defined URL belongs in which category
# if a URL has a viewable view, then if it is a part of home, leaderboard, profile, store, notifications, or modtools categories--
# then it will be placed in the appropriate category below
# THIS IS MAINLY USED TO HIGHLIGHT NAVBAR BUTTONS FOR NOW
def current_section(request):
    path = request.path
    if '/' == path:
        return {'current_section': 'home'}
    elif '/add_activity/' in path or '/activity/' in path or '/edit_activity/' in path:
        return {'current_section': 'home'}
    elif '/leaderboard/' in path:
        return {'current_section': 'leaderboard'}
    elif '/store/' in path or '/item/' in path or '/add_item/' in path or '/cart/' in path or '/checkout/' in path or '/edit_item_form/' in path:
        return {'current_section': 'store'}
    elif '/notifications/' in path:
        return {'current_section': 'notifications'}
    elif '/profile/' in path or '/edit_profile/' in path or '/teams/' in path:
        return {'current_section': 'profile'}
    # Add more conditions as necessary
    else:
        return {'current_section': None}
