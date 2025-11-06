def find_price_gap_pair(nums: list[int], k: int) -> tuple[int, int] | None:
    """
        Approach:
            1. Create a dictionary to map each value to its list of indices.
            2. Iterate through the list and for each value, calculate the target value (value - k or value + k).
            3. Check if the target value exists in the dictionary.
            4. If it exists, iterate through the list of indices for that target value and form pairs.
            5. Store unique pairs in a set to avoid duplicates.
            6. Finally, return the lexicographically smallest pair or None if no such pair exists.

        Time Complexity: O(n^2) in the worst case due to nested loops.
        Space Complexity: O(n) for the dictionary and set.
    """
    ans = set()
    value_to_index = {}
    
    for index, value in enumerate(nums):
        if value not in value_to_index:
            value_to_index[value] = []
        value_to_index[value].append(index)
    
    for index, value in enumerate(nums):
        if value<0: diff = value+k
        else: diff = value-k

        if diff in value_to_index:
            for index_diff in value_to_index[diff]:
                if index != index_diff:
                    pair = tuple(sorted([index, index_diff]))
                    ans.add(pair)

    if not ans:
        return None

    ans = sorted(list(ans))
    return ans[0]