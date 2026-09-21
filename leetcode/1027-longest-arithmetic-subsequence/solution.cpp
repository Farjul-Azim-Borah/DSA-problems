class Solution {
public:
    int longestArithSeqLength(vector<int>& nums) {
        int n = nums.size();
        vector<vector<int>> dp(n+1, vector<int>(1002, 0));
        int ans = 0; 
        for(int i = 0; i<n; ++i){
            for(int j = 0; j<i; ++j){
                int d = nums[i]-nums[j]+501;
                dp[i][d] = max(1 + dp[j][d], dp[i][d]);
                ans = max(ans, dp[i][d]);
            }
        }
        return ans+1; 
    }
};