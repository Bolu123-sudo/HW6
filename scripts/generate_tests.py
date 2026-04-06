import random
import string
from pathlib import Path

SEED = 4533
CASE_COUNT = 10
random.seed(SEED)

root = Path(__file__).resolve().parents[1]
data_dir = root / 'data'
data_dir.mkdir(parents=True, exist_ok=True)


def make_alphabet_pool():
    size = random.randint(5, 10)
    letters = random.sample(list(string.ascii_lowercase), size)
    letters.sort()
    return letters


def make_values(chars):
    return {ch: random.randint(1, 20) for ch in chars}


def patterned_word(chars, length):
    mode = random.choice(['uniform', 'bursty', 'motif', 'weighted'])

    if mode == 'uniform':
        return ''.join(random.choice(chars) for _ in range(length))

    if mode == 'bursty':
        out = []
        while len(out) < length:
            ch = random.choice(chars)
            run = random.randint(1, 5)
            out.extend(ch for _ in range(run))
        return ''.join(out[:length])

    if mode == 'motif':
        motif_len = random.randint(2, min(6, len(chars)))
        motif = ''.join(random.choice(chars) for _ in range(motif_len))
        out = []
        while len(out) < length:
            if random.random() < 0.6:
                out.extend(motif)
            else:
                out.append(random.choice(chars))
        return ''.join(out[:length])

    weights = [random.randint(1, 8) for _ in chars]
    return ''.join(random.choices(chars, weights=weights, k=length))


def mutate(source, chars, target_length):
    source_list = list(source)
    if source_list and random.random() < 0.7:
        for _ in range(random.randint(1, max(1, len(source_list) // 6))):
            idx = random.randrange(len(source_list))
            source_list[idx] = random.choice(chars)
    if source_list and random.random() < 0.5:
        start = random.randrange(len(source_list))
        stop = min(len(source_list), start + random.randint(2, 8))
        chunk = source_list[start:stop]
        random.shuffle(chunk)
        source_list[start:stop] = chunk
    if source_list and random.random() < 0.4:
        source_list = source_list[::-1]

    while len(source_list) < target_length:
        source_list.insert(random.randrange(len(source_list) + 1), random.choice(chars))
    while len(source_list) > target_length:
        del source_list[random.randrange(len(source_list))]
    return ''.join(source_list)


for idx in range(1, CASE_COUNT + 1):
    alphabet = make_alphabet_pool()
    scores = make_values(alphabet)

    left_len = random.randint(25, 120)
    right_len = random.randint(25, 120)

    shared_core = patterned_word(alphabet, random.randint(10, min(left_len, right_len)))
    left_noise = patterned_word(alphabet, max(0, left_len - len(shared_core)))
    right_noise = patterned_word(alphabet, max(0, right_len - len(shared_core)))

    left_mix = list(shared_core + left_noise)
    right_mix = list(shared_core + right_noise)
    random.shuffle(left_mix)
    random.shuffle(right_mix)

    left_word = mutate(''.join(left_mix), alphabet, left_len)
    right_word = mutate(''.join(right_mix), alphabet, right_len)

    with (data_dir / f'test{idx}.in').open('w', encoding='utf-8') as out:
        out.write(f"{len(alphabet)}\n")
        for ch in alphabet:
            out.write(f"{ch} {scores[ch]}\n")
        out.write(f"{left_word}\n{right_word}\n")

print(f'Generated {CASE_COUNT} varied test files in data/ using seed {SEED}.')
