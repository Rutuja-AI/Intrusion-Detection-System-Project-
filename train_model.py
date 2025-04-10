from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.class_weight import compute_class_weight
import pandas as pd
import pickle
import joblib

# 👑 Step 1: Define headers
columns = [
    'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
    'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins',
    'logged_in', 'num_compromised', 'root_shell', 'su_attempted',
    'num_root', 'num_file_creations', 'num_shells', 'num_access_files',
    'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count',
    'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate',
    'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
    'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
    'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
    'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate',
    'dst_host_serror_rate', 'dst_host_srv_serror_rate',
    'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'label', 'difficulty'
]

# 🧠 Step 2: Load CSV with header manually
df = pd.read_csv("KDDTrain+.csv", names=columns)

# 🧼 Step 3: Drop the difficulty column
df = df.drop(columns=["difficulty"])


# Only drop 'difficulty' if it exists
if "difficulty" in df.columns:
    df = df.drop(columns=["difficulty"])

# Only one-hot encode if those columns exist
for col in ["protocol_type", "service", "flag"]:
    if col in df.columns:
        df = pd.get_dummies(df, columns=[col])

if "label" not in df.columns:
    print("🚨 Column 'label' not found! Available columns:")
    print(df.columns.tolist())
    exit()

X = df.drop("label", axis=1)
y = df["label"]

# Class weights
classes = y.unique()
weights = compute_class_weight(class_weight='balanced', classes=classes, y=y)
class_weights = dict(zip(classes, weights))

model = RandomForestClassifier(class_weight=class_weights)
model.fit(X, y)

with open("rf_model.joblib", "wb") as f:
    joblib.dump(model, f)

with open("columns.txt", "w") as f:
    for col in X.columns:
        f.write(col + "\n")

print("✅ New model trained with balanced classes!")
