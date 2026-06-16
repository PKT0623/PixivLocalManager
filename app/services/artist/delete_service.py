from app.database.artist import ArtistRepository
from app.services.artist.validation import validate_artist_ids
from app.services.backup import BackupService


class ArtistDeleteService:
    def __init__(self):
        self.repo = ArtistRepository()
        self.backup_service = BackupService()

    def delete_artist(self, artist_id: int):
        return self.delete_artists([artist_id])

    def delete_artists(self, artist_ids: list[int]) -> str:
        validate_artist_ids(artist_ids)

        backup_path = self.backup_service.export_deleted_artists_backup(
            artist_ids
        )

        self.repo.delete_artists(artist_ids)

        return backup_path

    def restore_deleted_artists_backup(
        self,
        file_path: str,
    ) -> dict:
        return self.backup_service.restore_deleted_artists_backup(
            file_path
        )
