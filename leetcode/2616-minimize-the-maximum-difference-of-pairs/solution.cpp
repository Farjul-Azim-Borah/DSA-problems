class Solution {
public:
    bool can(vector<int>& nums, int p, int mid) {
        int count = 0;
        for (int i = 1; i < nums.size(); i++) {
            if (nums[i] - nums[i-1] <= mid) {
                count++;
                i++;
            }
        }
        return count >= p;
    }

    int minimizeMax(vector<int>& nums, int p) {
        sort(nums.begin(), nums.end());

        int l = 0, r = nums.back() - nums.front();
        int ans = r;

        while (l <= r) {
            int mid = (l + r) / 2;

            if (can(nums, p, mid)) {
                ans = mid;
                r = mid - 1;
            } else {
                l = mid + 1;
            }
        }

        return ans;
    }
};
