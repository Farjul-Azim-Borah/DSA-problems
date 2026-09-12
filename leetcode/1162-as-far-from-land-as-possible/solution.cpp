class Solution {
public:
    int maxDistance(vector<vector<int>>& grid) {
        int n = grid.size();
        int ans = 0;
        queue<pair<int, int>>q;
        for(int i = 0; i<n; ++i){
            for(int j = 0; j<n; ++j){
                if(grid[i][j] == 1){
                    q.push({i, j});
                }
            }
        }
        if(q.empty() or q.size() == n*n){
            return -1;
        }
        int dirx[4] = {-1, 0, 1, 0};
        int diry[4] = {0, -1, 0, 1};
        while(!q.empty()){
            int sz = q.size();
            for(int s = 0; s<sz; ++s){
                auto [x, y] = q.front();
                q.pop();
                for(int k = 0; k<4; ++k){
                    int x_n = dirx[k] + x;
                    int y_n = diry[k] + y;
                    if(x_n >= 0 && y_n >= 0 && x_n < n && y_n < n && grid[x_n][y_n] == 0){
                        q.push({x_n, y_n});
                        grid[x_n][y_n] = 1;
                    }
                }
            }
            ans++;
        }
        return ans-1;
    }
};