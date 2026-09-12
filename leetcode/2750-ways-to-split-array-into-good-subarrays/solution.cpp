class Solution {
public:
    int numberOfGoodSubarraySplits(vector<int>& nums) {
        int n = nums.size();
        for(int i = 1; i<n; ++i){
            nums[i] += nums[i-1];
        }
        if(nums[n-1] == 0){
            return 0;
        }
        map<int, int> mp;
        for(auto i : nums){
            mp[i]++;
        }
        (--mp.end())->second = 1;
        long long ans = 1;
        int mod = 1e9+7;
        for(auto [x, y] : mp){
            if(x == 0){
                continue;
            }
            ans = (1ll*ans*y)%mod;
        }
        return ans;
    }
};