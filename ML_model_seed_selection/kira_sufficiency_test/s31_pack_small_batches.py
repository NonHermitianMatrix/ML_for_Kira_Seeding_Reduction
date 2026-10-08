"""Pack at most four independent small systems while preserving all equations."""
from s27_retry_small_batches import small_batches
def packed_batches(blocks):
 batch=[];count=0
 for single in small_batches(blocks):
  piece=single[0];size=len(piece["equations"])+len(piece["targets"])
  if batch and (len(batch)>=4 or count+size>2000):
   yield batch;batch=[];count=0
  batch.append(piece);count+=size
 if batch:yield batch
