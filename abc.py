from sklearn.preprocessing import LabelEncoder
import joblib

encoder = joblib.load("data/new_featured/festival_encoder.pkl")
festival_list = list(encoder.classes_)
print(festival_list)