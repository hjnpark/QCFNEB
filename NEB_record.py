import qcportal as ptl # Importing QCPortal
import numpy as np


# Connecting to the server
client = ptl.PortalClient('https://address', verify=False, username = 'usrname', password= 'password', cache_dir='./')


# Printing all the available datasets
print(client.list_datasets_table())


# RGD1 dataset 
ds = client.get_dataset('neb',
                        dataset_name='neb_RGD_commit4',
                        )


# We can iterate all the records in the dataset
print('\nIterating through NEB records and printing the entry name, specification name, and record for up to 10 entries.')
count = 0 
for ent, spec, rec in ds.iterate_records():
    if count == 10:
        break
    print(ent, spec, rec)
    count += 1


# We can also return one specific record
neb_rec = ds.get_record(entry_name='RGD1_A', specification_name='0000_A_b')


# Printing the specifications used for the calculations
print('\nNEB specifications: ')
print(neb_rec.specification)


# Initial and final chains 
initial_chain = neb_rec.initial_chain # This is a list of Molecule objects 
final_chain = neb_rec.final_chain # This is a list of Singlepoint records for the final chain
print('\nGeometry comparison of a frame before and after NEB')
print('Before: ', initial_chain[3].geometry) # Geometry of the 4th frame from the initial chain
print('After: ', final_chain[3].molecule.geometry) # Geometry of the 4th frame from the final chain


# All Singlepoint (SP) records carried during the NEB calculation as a dictionary
neb_sps= neb_rec.singlepoints  
*_, final_sps = neb_sps.values() # A list of the SP records for the last chain
sp = final_sps[0] # The SP record of the first frame from the last chain
print('\nGradients from a Singlepoint record: ')
print(sp.return_result) # Printing gradients. 
print('Full Singlepoint record: ')
print(sp.to_qcschema_result) # Printing more details of the record

for sp1, sp2 in zip(final_chain, final_sps):
    # The gradients of the SP records from neb_rec.final_chain and neb_rec.singlepoints should be identical 
    assert np.all(sp1.return_result == sp2.return_result)     


# Saving geometry of the highest energy image
highest_E = -np.inf
for sp in final_sps:
    current_E = sp.properties['current energy']
    if current_E > highest_E:
        highest_E = current_E
        highest_E_geometry = sp.molecule.geometry


# The result of the NEB calculation is a Molecule object representing the highest energy image from the final chain
neb_result = neb_rec.result

# The geometry of the highest energy image and that of the NEB result should be identical
assert np.all(highest_E_geometry == neb_result.geometry)


# Optimization records
neb_opts = neb_rec.optimizations

initial = neb_opts.get('initial') # Optimization record for the first frame of the initial chain
final = neb_opts.get('final') # Optimization record for the last frame of the initial chain
ts = neb_opts.get('transition') # TS Optimization record for the highest energy frame of the final chain  

ts_traj = ts.trajectory # Optimization progress as a list with Singlepoint records

optimized_TS = ts_traj[-1] # Singlepoint record of the optimized TS structure


# Hessian of the optimized TS structure

ds_hessian = client.get_dataset('singlepoint',
                                dataset_name='Hessian_commit4',
                                )
hessian_rec = ds_hessian.get_record('0000_A_b','b3lyp')

print('\nCalculated Hessian: ')
print(hessian_rec.return_result)

# The geometry of the optimized TS structure should be identical to that used for the Hessian calculation. 
assert np.all(hessian_rec.molecule.geometry == optimized_TS.molecule.geometry)


# Uncommenting the following three lines will print standard outputs 
#print(neb_rec.stdout) # NEB
#print(ts.stdout) # TS optimization
#print(optimized_TS.stdout) # Singlepoint record of the optimized TS


