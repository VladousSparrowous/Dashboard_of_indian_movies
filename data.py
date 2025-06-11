import kagglehub
from kagglehub import KaggleDatasetAdapter
from pathlib import Path

app_dir = Path(__file__).parent
print(app_dir)
file_path = "Data for repository.csv"


df = kagglehub.load_dataset(
  KaggleDatasetAdapter.PANDAS,
  "ishajangir/bollywood-movies",
  file_path,
)
