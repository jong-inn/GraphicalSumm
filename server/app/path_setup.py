from pathlib import Path

DATA_PATH = Path('./data/audio/raw')

def main():
    
    if not DATA_PATH.exists():
        DATA_PATH.mkdir(parents=True)
        print(f"{DATA_PATH} is created.")

if __name__ == '__main__':
    
    main()