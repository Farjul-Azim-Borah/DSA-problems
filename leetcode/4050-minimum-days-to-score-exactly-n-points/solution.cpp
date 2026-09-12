class Solution {
public:
    int minDays(int n) {

        vector<int> dp(n + 1, 1e9);

        dp[n] = 0;

        for (int i = n - 1; i >= 0; i--) {

            for (int k = 1; k * (k + 1) / 2 <= n; k++) {

                int points = k * (k + 1) / 2;
                if(i+points > n){
                    break;
                }

                dp[i] = min(dp[i],
                            dp[i + points] + k + 1);
            }
        }

        return dp[0]-1;
    }
};