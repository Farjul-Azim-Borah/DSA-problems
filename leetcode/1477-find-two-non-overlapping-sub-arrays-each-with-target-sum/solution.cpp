class Solution {
public:
    int minSumOfLengths(vector<int>& arr, int target) {
        int n = arr.size();
        const int INF = 1e9;

        vector<int> dp(n, INF);

        unordered_map<int, int> mp;

        int sum = 0;
        int best = INF;
        int ans = INF;

        for (int i = 0; i < n; i++) {
            sum += arr[i];

            if (i > 0)
                dp[i] = dp[i - 1];

            if (sum == target) {
                int len = i + 1;
                dp[i] = min(dp[i], len);
            }

            if (mp.count(sum - target)) {
                int j = mp[sum - target];

                int len = i - j;

                if ( dp[j] != INF) {
                    ans = min(ans, len + dp[j]);
                }

                dp[i] = min(dp[i], len);
            }

            mp[sum] = i;
        }

        return ans == INF ? -1 : ans;
    }
};