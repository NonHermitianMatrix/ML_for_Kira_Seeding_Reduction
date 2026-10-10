# Shared exact payloads

Each compressed object has the SHA256 of its canonical decoded JSON as its filename. Workflow records refer to these objects with _shared_payload. Read records with s04_workflows.read, which verifies hashes and restores all exact coefficients, exports and input data. Saving a workflow checks a lossless round trip. This storage format reduces repeated bytes without dropping failed attempts or physical evidence.
