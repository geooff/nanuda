from fastai.learner import load_learner

learn = load_learner("all-emoji-sample-40")
labels = learn.dls.vocab[1]


def serve(predicte, max_n=5):
    confidences = learn.predict(predicte)[
        2
    ].tolist()  # Get List of predictions from fastai
    results = {
        l: c for l, c in zip(labels, confidences)
    }  # Wrap labels and confidences into dictionary
    results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    top_results = results[:max_n]
    total_confidence = sum([x[1] for x in top_results])
    return top_results, total_confidence


serve("RIP lil peep")