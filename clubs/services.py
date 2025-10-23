from blockchain.anoma_service import publish_intent
def create_club(name, owner_wallet):
    intent = {'type':'mint_club_nft','name':name,'owner':owner_wallet}
    return publish_intent(intent)
