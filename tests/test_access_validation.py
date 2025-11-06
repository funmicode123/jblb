import pytest
from unittest.mock import patch, MagicMock
from clubs.models import Club
from battles.validator import validate_player_access   # ← your real function


@pytest.mark.django_db
class TestAccessValidation:
    @pytest.fixture
    def club(self):
        return Club.objects.create(
            name="Test Club",
            category="rare",
            owner_wallet="0xOWNER123",
            tier="RARE",
            access_type="private",      # ← matches your model
            privileges="exclusive chat"
        )

    @pytest.fixture
    def player(self):
        p = MagicMock()
        p.id = 999
        p.wallet = "0xABC123"          # ← validator uses .wallet
        p.wallet_address = "0xABC123"  # ← fallback
        p.nft_token_id = "0.0.5555/1"
        return p

    # 1. Public = instant win
    def test_public_club_access(self, club, player):
        club.access_type = "public"
        club.save()
        assert validate_player_access(player, club) is True

    # 2. Already a member = skip NFT
    @patch("battles.validator.Club.players")
    def test_existing_member_access(self, mock_players, club, player):
        club.access_type = "private"
        club.save()
        mock_players.filter.return_value.exists.return_value = True
        assert validate_player_access(player, club) is True

    # 3. NFT checks pass
    @patch("blockchain.services.hedera_service.validate_nft_ownership", return_value=True)
    @patch("blockchain.utils.hedera_utils.verify_nft_access", return_value=True)
    @patch("battles.validator.Club.players")
    def test_valid_nft_access(self, mock_players, mock_verify, mock_owns, club, player):
        club.access_type = "private"
        club.save()
        mock_players.filter.return_value.exists.return_value = False
        assert validate_player_access(player, club) is True
        mock_owns.assert_called_once()
        mock_verify.assert_called_once()

    # 4. No NFT token → boom
    @patch("battles.validator.Club.players")
    def test_missing_nft_token(self, mock_players, club, player):
        player.nft_token_id = None
        club.access_type = "private"
        club.save()
        mock_players.filter.return_value.exists.return_value = False
        with pytest.raises(ValueError):
            validate_player_access(player, club)

    # 5. Wrong owner → boom
    @patch("blockchain.services.hedera_service.validate_nft_ownership", return_value=False)
    @patch("battles.validator.Club.players")
    def test_invalid_nft_ownership(self, mock_players, mock_owns, club, player):
        club.access_type = "private"
        club.save()
        mock_players.filter.return_value.exists.return_value = False
        with pytest.raises(PermissionError):
            validate_player_access(player, club)
