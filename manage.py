import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "장고가 설치되어 있는지 확인하세요요"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()