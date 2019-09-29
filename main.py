import sys
from backup_manager import BackupManager


if __name__ == "__main__":

    if len(sys.argv) > 1:
        bm = BackupManager(sys.argv[1])
    else:
        argv1 = input("Введите название проекта: ")
        bm = BackupManager(argv1)
    bm.backup()
