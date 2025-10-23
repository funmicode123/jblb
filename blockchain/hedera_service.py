import os, datetime
HEDERA_OPERATOR_ID = os.getenv('HEDERA_OPERATOR_ID')
HEDERA_OPERATOR_KEY = os.getenv('HEDERA_OPERATOR_KEY')
def publish_to_hcs(topic_id, message):
    return {'topic_id': topic_id or 'mock-topic', 'message': message, 'published_at': datetime.datetime.utcnow().isoformat()}
def create_fungible_token(name='JBLB Test', symbol='JBLB', initial_supply=1000000):
    return {'token_id': '0.0.' + str(abs(hash(name)) % 1000000), 'name': name, 'symbol': symbol, 'supply': initial_supply}
