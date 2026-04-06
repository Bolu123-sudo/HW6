#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>

struct SolveReport {
    long long best_score;
    std::string picked_sequence;
};

struct ProblemInstance {
    std::unordered_map<char, long long> letter_score;
    std::string left_word;
    std::string right_word;
};

static bool load_problem(std::istream& input, ProblemInstance& job) {
    int alphabet_count = 0;
    if (!(input >> alphabet_count)) {
        return false;
    }

    job.letter_score.clear();
    for (int i = 0; i < alphabet_count; ++i) {
        char symbol = '\0';
        long long weight = 0;
        if (!(input >> symbol >> weight)) {
            return false;
        }
        job.letter_score[symbol] = weight;
    }

    if (!(input >> job.left_word >> job.right_word)) {
        return false;
    }
    return true;
}

static long long score_of(char ch, const std::unordered_map<char, long long>& score_book) {
    auto it = score_book.find(ch);
    return (it == score_book.end()) ? 0LL : it->second;
}

static SolveReport solve_weighted_common_subsequence(const ProblemInstance& job) {
    const std::size_t rows = job.left_word.size();
    const std::size_t cols = job.right_word.size();

    std::vector<std::vector<long long>> best(rows + 1, std::vector<long long>(cols + 1, 0));

    for (std::size_t r = 1; r <= rows; ++r) {
        for (std::size_t c = 1; c <= cols; ++c) {
            best[r][c] = std::max(best[r - 1][c], best[r][c - 1]);

            if (job.left_word[r - 1] == job.right_word[c - 1]) {
                const long long gain = score_of(job.left_word[r - 1], job.letter_score);
                best[r][c] = std::max(best[r][c], best[r - 1][c - 1] + gain);
            }
        }
    }

    std::string recovered;
    std::size_t r = rows;
    std::size_t c = cols;

    while (r > 0 && c > 0) {
        if (job.left_word[r - 1] == job.right_word[c - 1]) {
            const long long gain = score_of(job.left_word[r - 1], job.letter_score);
            if (best[r][c] == best[r - 1][c - 1] + gain) {
                recovered.push_back(job.left_word[r - 1]);
                --r;
                --c;
                continue;
            }
        }

        if (best[r - 1][c] >= best[r][c - 1]) {
            --r;
        } else {
            --c;
        }
    }

    std::reverse(recovered.begin(), recovered.end());
    return {best[rows][cols], recovered};
}

int main(int argc, char* argv[]) {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    ProblemInstance job;

    if (argc == 2) {
        std::ifstream file(argv[1]);
        if (!file) {
            std::cerr << "Error: unable to open input file: " << argv[1] << '\n';
            return 1;
        }
        if (!load_problem(file, job)) {
            std::cerr << "Error: malformed input.\n";
            return 1;
        }
    } else {
        if (!load_problem(std::cin, job)) {
            std::cerr << "Error: malformed input.\n";
            return 1;
        }
    }

    const SolveReport answer = solve_weighted_common_subsequence(job);
    std::cout << answer.best_score << '\n' << answer.picked_sequence << '\n';
    return 0;
}
