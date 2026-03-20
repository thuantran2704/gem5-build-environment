#include <bits/stdc++.h>
using namespace std;

typedef pair<int, int> pii;

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Usage: ./my_program input.txt\n";
        return 1;
    }

    ifstream infile(argv[1]);
    int n, m;
    infile >> n >> m;

    vector<vector<pii>> adj(n);

    for (int i = 0; i < m; i++) {
        int u, v, w;
        infile >> u >> v >> w;
        adj[u].push_back({v, w});
    }

    int source = 0;
    vector<int> dist(n, INT_MAX);
    priority_queue<pii, vector<pii>, greater<pii>> pq;

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();

        if (d > dist[u]) continue;

        for (auto [v, w] : adj[u]) {
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                pq.push({dist[v], v});
            }
        }
    }

    // Print result (important for correctness check)
    for (int i = 0; i < n; i++) {
        cout << dist[i] << " ";
    }
    cout << endl;

    return 0;
}