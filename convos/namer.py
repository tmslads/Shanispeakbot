# Function to choose your nickname-


def nicknamer(update, context):
    """Uses current nickname set by user."""

    try:
        name = context.user_data['nickname'][-1]
    except (KeyError, IndexError):
        context.user_data['nickname'] = []
        context.user_data['nickname'].append(update.message.from_user.first_name)
    finally:
        return context.user_data['nickname'][-1]
