class Solution {
public:
    vector<vector<int>> dp;

    int solve(int i, int j, vector<int>& stones, vector<int>& pref) {
        if (i >= j) {
            return 0;
        }

        if (dp[i][j] != -1) {
            return dp[i][j];
        }

        int leftSum = pref[j + 1] - pref[i + 1];
        int rightSum = pref[j] - pref[i];

        int removeLeft = leftSum - solve(i + 1, j, stones, pref);
        int removeRight = rightSum - solve(i, j - 1, stones, pref);

        return dp[i][j] = max(removeLeft, removeRight);
    }

    int stoneGameVII(vector<int>& stones) {
        int n = stones.size();

        vector<int> pref(n + 1, 0);

        for (int i = 0; i < n; i++) {
            pref[i + 1] = pref[i] + stones[i];
        }

        dp.assign(n, vector<int>(n, -1));

        return solve(0, n - 1, stones, pref);
    }
};