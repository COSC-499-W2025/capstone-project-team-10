from src.log import log
from src.fas.fas import FileAnalysis
import time
import threading

# Initialize (open_log_file will create the log directory)
log.open_log_file()

# Create test data
test_obj1 = FileAnalysis(
    file_path="test/path1.txt",
    file_name="test1.txt",
    file_type="txt",
    last_modified="2026-01-25T12:00:00",
    created_time="2026-01-25T11:00:00",
    extra_data="TEST_DATA_1",
)

test_obj2 = FileAnalysis(
    file_path="test/path2.doc",
    file_name="test2.doc",
    file_type="doc",
    last_modified="2026-01-25T13:00:00",
    created_time="2026-01-25T12:30:00",
    extra_data="TEST_DATA_2",
)

test_obj3 = FileAnalysis(
    file_path="test/path3.pdf",
    file_name="test3.pdf",
    file_type="pdf",
    last_modified="2026-01-25T14:00:00",
    created_time="2026-01-25T13:45:00",
    extra_data="TEST_DATA_3",
)

# Write initial entries - this will populate the log with the first 2 objs
log.write(test_obj1)
log.write(test_obj2)

# Start background thread that appends more lines - this is to simulate that the user is doing more writings in the background
def append_more():
    time.sleep(1)  # Wait 1 second
    print("[Thread] Appending new entry...")
    log.write(test_obj3)
    time.sleep(0.5)
    # In fact - you can write more things over here - and another test_obj, or edit the test_obj3 in order to see the differences
    # Remember to add another time.sleep(<time>) for responsive tactile
    print("[Thread] Writing close signal...")
    with open(log.current_log_file, "a") as f:
        f.write("!close!\n")

thread = threading.Thread(target=append_more, daemon=True) # daemon as it terminates as soon as the job is finished
thread.start()

# Follow the log (will block until !close!)
print("[Main] Starting to follow log...")
for line in log.follow_log(include_header=False):
    print(f"[Main] Got: {line}")

print("[Main] Done!")