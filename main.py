import os
import requests
import json

username = str(os.getenv('USERNAME', 'anonymous'))
nice_version = os.getenv('NICE_VERSION', 'unknown')

def numberToBase(n, b): # represent a number n in base b
    # returns a list of digits from MSD to LSD
    # c/o stackoverflow, because numpy base_repr only goes up to base 36
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return digits[::-1]

def get_num_uniques(num, base): # get the number of unique digits in the sqube
    # get the square and cube, then represent them in the selected base
    n_square = numberToBase(num**2, base)
    n_cube = numberToBase(num**3, base)
    # get the number of unique values in the concatenation
    return len(set(n_square + n_cube))

def search_range(n_start, n_end, base): # search a range of numbers
    qty_uniques = {} # the quantity of numbers with each possible niceness
    near_misses = {} # numbers with niceness >= 0.9
    uniques_cutoff = base*0.9
    for b in range(1,base+1):
        qty_uniques.update({b: 0})
    for num in range(n_start, n_end):
        num_uniques = get_num_uniques(num, base)
        if num_uniques >= uniques_cutoff:
            near_misses[num] = get_num_uniques(num, base)
        qty_uniques[num_uniques]+=1
    return qty_uniques, near_misses

def main():
    # get the next available search field
    claimResponse = requests.get('https://nice.wasabipesto.com/claim?username='+username)
    claimResponse.raise_for_status()
    claimResponse = claimResponse.json()
    print(
        'Checked out field ID', claimResponse['search_id'], 
        'from', claimResponse['search_start'], 
        'to', claimResponse['search_end'], 
        'in base', claimResponse['base']
    )
    
    # do the search
    qty_uniques, near_misses = search_range(
        claimResponse['search_start'], 
        claimResponse['search_end'], 
        claimResponse['base']
    )
    
    submitData = {
        'search_id': claimResponse['search_id'],
        'username': username,
        'client_version': nice_version,
        'unique_count': qty_uniques,
        'near_misses': near_misses
    }

    # send results to mothership
    print('Submitting results of field ID', claimResponse['search_id'], 'as', username)
    submitResponse = requests.post('https://nice.wasabipesto.com/submit',json=submitData)
    try:
        submitResponse.raise_for_status()
    except:
        raise Exception(submitResponse.text)

if __name__ == '__main__':
    print('Staring nice-client version', nice_version)
    while True:
        main()
