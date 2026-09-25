class Solution {
public:
    int longestSubarray(vector<int>& nums) {
        int mx = *max_element(nums.begin(), nums.end());
        int ans = 0, count = 0; 
        for(auto i : nums){
            if(i == mx){
                count++;
            }else{
                ans = max(ans, count);
                count = 0;
            }
        }
        ans = max(ans, count);
        return ans;

    }
};