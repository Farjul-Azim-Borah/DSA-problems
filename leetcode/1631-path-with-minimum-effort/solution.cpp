class Solution {
public:
    bool solve(int mid, vector<vector<int>>& h){
        int n = h.size(), m = h[0].size();
        int dix[4] = {-1, 0, 1, 0};
        int diy[4] = {0, -1, 0, 1};
        queue<pair<int, int>>q;
        q.push({0, 0});
        vector<vector<int>> vis(n, vector<int>(m, 0));
        while(!q.empty()){
            int a = q.front().first, b = q.front().second;
            if(a == n-1 && b == m-1){
                return true;
            }
            q.pop();
            for(int i = 0; i<4; ++i){
                int x = a + dix[i];
                int y = b + diy[i];
                if(x >= 0 && y >= 0 && x < n && y < m && vis[x][y] == 0){
                    if(abs(h[x][y]-h[a][b]) <= mid){
                        vis[x][y] = 1;
                        q.push({x, y});
                    }
                }
            }
        }
        return false;
    }
    int minimumEffortPath(vector<vector<int>>& h) {
        long long l = 0, r = 1e7;
        int ans = 0; 
        while(r >= l){
            long long mid = (l + r)/2;
            if(solve(mid, h)){
                ans = mid;
                r = mid-1;
            }else{
                l = mid+1;
            }
        }
        return ans;
    }
};