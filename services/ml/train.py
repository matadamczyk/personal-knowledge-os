import os
import json
import numpy as np
from fastembed import TextEmbedding

CATEGORIES = [
    "FastAPI",
    "Python",
    "Vue",
    "DevOps",
    "Machine Learning",
    "System Design",
    "Bug Fix",
    "Research",
    "Personal",
    "Business Ideas"
]

DATASET = [
    # FastAPI
    {"category": "FastAPI", "title": "FastAPI CORS setup", "content": "How to set up CORSMiddleware in FastAPI to allow cross-origin requests."},
    {"category": "FastAPI", "title": "API Router prefixes", "content": "Structuring routes using APIRouter and prefix parameter in FastAPI."},
    {"category": "FastAPI", "title": "FastAPI dependency injection", "content": "Using Depends to manage database sessions and dependencies in path operations."},
    {"category": "FastAPI", "title": "HTTPException error handling", "content": "Raising HTTPExceptions with custom status codes and detail in FastAPI API routes."},
    {"category": "FastAPI", "title": "Pydantic body validation", "content": "Validating incoming JSON request bodies using Pydantic schemas in FastAPI endpoints."},
    {"category": "FastAPI", "title": "Async endpoints in FastAPI", "content": "Writing asynchronous path functions with async def and using await for non-blocking I/O."},
    {"category": "FastAPI", "title": "Uvicorn server configurations", "content": "Configuring uvicorn, fastapi-cli, and workers for deploying FastAPI applications."},
    
    # Python
    {"category": "Python", "title": "Python list comprehensions", "content": "Sleek list comprehensions, generator expressions, and dictionary mappings in Python."},
    {"category": "Python", "title": "Understanding Python decorators", "content": "Writing custom decorators, wrapper functions, and using functools.wraps in Python."},
    {"category": "Python", "title": "Python context managers", "content": "Creating context managers using the with statement and contextmanager decorator in Python."},
    {"category": "Python", "title": "Inheritance and MRO in Python", "content": "Understanding multiple inheritance and the method resolution order using super() in Python."},
    {"category": "Python", "title": "Dataclasses in Python 3.7+", "content": "Using the @dataclass decorator to generate constructors, string representations, and comparisons."},
    {"category": "Python", "title": "Concurrency in Python", "content": "Comparing multithreading, multiprocessing, and asyncio for I/O and CPU bound tasks in Python."},
    {"category": "Python", "title": "Advanced Python slicing", "content": "Manipulating lists, tuples, and strings using stride and start/stop slices in Python."},
    
    # Vue
    {"category": "Vue", "title": "Vue 3 script setup", "content": "Getting started with the Composition API and setup script format in Vue components."},
    {"category": "Vue", "title": "Reactive Vue variables", "content": "Comparing ref and reactive to declare local state in Vue 3 applications."},
    {"category": "Vue", "title": "Component props and emits", "content": "Declaring props using defineProps and custom events using defineEmits in Vue 3."},
    {"category": "Vue", "title": "Vue Router history mode", "content": "Configuring createWebHistory, route mapping, and navigation guard triggers in Vue Router."},
    {"category": "Vue", "title": "Pinia state management store", "content": "Defining global state, getters, and actions using defineStore in Pinia for Vue apps."},
    {"category": "Vue", "title": "Vue 3 lifecycle hooks", "content": "Using hooks like onMounted, onUnmounted, and watchEffect to control component side effects."},
    {"category": "Vue", "title": "Custom Vue directives", "content": "Creating custom directives and dynamically rendering components with dynamic components in Vue."},
    
    # DevOps
    {"category": "DevOps", "title": "Docker Compose multi-container", "content": "Setting up multi-container local environments using docker-compose.yml files and networks."},
    {"category": "DevOps", "title": "Multi-stage Dockerfile builds", "content": "Optimizing Docker image size by compiling code in builder stages and copying artifacts."},
    {"category": "DevOps", "title": "GitHub Actions CI/CD workflows", "content": "Building and testing applications automatically using YAML workflow configuration files on GitHub."},
    {"category": "DevOps", "title": "Nginx reverse proxy configurations", "content": "Configuring Nginx server blocks for SSL termination, reverse proxies, and gzip compression."},
    {"category": "DevOps", "title": "Kubernetes manifest deployment", "content": "Writing YAML configurations for Kubernetes Pods, Deployments, and LoadBalancer Services."},
    {"category": "DevOps", "title": "Linux systemd background services", "content": "Writing a systemd service file to manage and restart Python daemon processes on server reboot."},
    {"category": "DevOps", "title": "Bash scripting for automated tasks", "content": "Writing bash shell scripts for database backups, file pruning, and cron job scheduling."},
    
    # Machine Learning
    {"category": "Machine Learning", "title": "Keras neural network training", "content": "Building and training multi-layer perceptron (MLP) classification models using Keras and TensorFlow."},
    {"category": "Machine Learning", "title": "Supervised learning paradigms", "content": "Understanding classification, regression, and standard loss functions like cross-entropy and MSE."},
    {"category": "Machine Learning", "title": "NLP feature engineering", "content": "Text representation techniques: bag-of-words, TF-IDF, Word2Vec, and transformer embeddings."},
    {"category": "Machine Learning", "title": "Gradient descent optimizers", "content": "Comparing stochastic gradient descent (SGD), Adam, and RMSprop optimization algorithms in backpropagation."},
    {"category": "Machine Learning", "title": "Classifier metrics evaluation", "content": "Calculating accuracy, precision, recall, F1-score, and plotting confusion matrices for predictions."},
    {"category": "Machine Learning", "title": "Fine-tuning LLM transformers", "content": "Adapting pre-trained huggingface transformers for custom text sequence classification tasks."},
    {"category": "Machine Learning", "title": "CNN spatial feature extraction", "content": "How convolution operations, pooling layers, and filters process image pixels in computer vision."},
    
    # System Design
    {"category": "System Design", "title": "Distributed token-bucket rate limiter", "content": "Designing high-scale API rate limiters using sliding windows or token bucket algorithms in Redis."},
    {"category": "System Design", "title": "Microservices vs Monolith architectures", "content": "Analyzing architectural trade-offs: data isolation, deployment velocity, and networking overhead."},
    {"category": "System Design", "title": "Consistent hashing caching layer", "content": "Scaling cache clusters using consistent hashing algorithms to minimize re-mapping of data keys."},
    {"category": "System Design", "title": "Database sharding and replication", "content": "Horizontal partitioning techniques and master-slave setups for scaling read/write database transactions."},
    {"category": "System Design", "title": "Message queue designs (Kafka/RabbitMQ)", "content": "Publish-subscribe models, partition counts, consumer groups, and message durability in message brokers."},
    {"category": "System Design", "title": "Scaling databases: Horizontal vs Vertical", "content": "Understanding memory expansion limitations vs network overhead when partition routing databases."},
    {"category": "System Design", "title": "Caching strategies", "content": "Comparing cache-aside, write-through, and write-behind cache architectures for speed and consistency."},
    
    # Bug Fix
    {"category": "Bug Fix", "title": "Fixing NullPointerException", "content": "Resolving database runtime exceptions by verifying nullable constraints and using Optional in ORM queries."},
    {"category": "Bug Fix", "title": "Resolving CORS origin blocked", "content": "Fixing web frontend errors by specifying correct Access-Control-Allow-Origin headers on servers."},
    {"category": "Bug Fix", "title": "Debugging JS memory leaks", "content": "Using chrome devtools heap snapshots to locate memory leaks in event listeners and intervals."},
    {"category": "Bug Fix", "title": "Database connection pool exhaustion", "content": "Resolving connection leaks by ensuring database sessions are properly closed using context managers."},
    {"category": "Bug Fix", "title": "Resolving Git merge conflicts", "content": "Locating conflict markers and performing git rebase to clean branch linear histories."},
    {"category": "Bug Fix", "title": "React hydration mismatch error", "content": "Fixing differences between server-side HTML output and client-side initial DOM hydration tree."},
    {"category": "Bug Fix", "title": "Python segment faults debugging", "content": "Using gdb and python faulthandler module to locate native segfaults in C extensions."},
    
    # Research
    {"category": "Research", "title": "Quantum search algorithms", "content": "Analyzing Shor's factoring and Grover's search algorithms on theoretical quantum architectures."},
    {"category": "Research", "title": "State of the art LLM review", "content": "A literature review of recent architecture trends in Large Language Models and mixture of experts (MoE)."},
    {"category": "Research", "title": "Graph database benchmarks", "content": "Research study comparing Neo4j, relational database recursive queries, and key-value graphs."},
    {"category": "Research", "title": "Theoretical cryptography review", "content": "Analysis of key exchange protocols, RSA prime number distributions, and post-quantum encryption standards."},
    {"category": "Research", "title": "Distributed consensus protocols (Paxos/Raft)", "content": "Rigorous comparison of safety proofs and cluster leader election processes in Paxos and Raft."},
    {"category": "Research", "title": "Neural network scaling limits", "content": "Scientific literature analysis on compute, token volume, and weight scaling bounds in deep learning."},
    {"category": "Research", "title": "Vector databases architectural comparison", "content": "Study of HNSW index structures, quantizations, and retrieval times in modern vector store libraries."},
    
    # Personal
    {"category": "Personal", "title": "Weekly grocery shopping list", "content": "Eggs, milk, sourdough bread, organic tomatoes, fresh spinach, coffee beans, and toilet paper."},
    {"category": "Personal", "title": "Daily workout split routine", "content": "Monday chest and triceps, Wednesday back and biceps, Friday legs and shoulders, plus core work."},
    {"category": "Personal", "title": "Mindfulness and life balance thoughts", "content": "Taking breaks, walking in nature, reading fiction, and journaling every evening for mental clarity."},
    {"category": "Personal", "title": "Family birthday gift ideas", "content": "Leather notebook for mom, smart watch strap for dad, and board games for my sister's birthday."},
    {"category": "Personal", "title": "Packing checklist for holiday", "content": "Passports, charger cords, sunglasses, swimming wear, travel adapter, tooth brush, and sneakers."},
    {"category": "Personal", "title": "Quarterly habits check-in", "content": "Tracking running mileage, sleep duration targets, and limiting screen time after 9 PM."},
    {"category": "Personal", "title": "Key takeaways from monthly reading", "content": "Reviewing atomic habits and list of habits to start building this week: hydration and early morning walks."},
    
    # Business Ideas
    {"category": "Business Ideas", "title": "Fitness center management SaaS", "content": "A subscription software for local gyms to track class bookings, member check-ins, and payments."},
    {"category": "Business Ideas", "title": "Subscription box pet snacks startup", "content": "A monthly organic pet food box containing customized healthy snacks based on breed size and age."},
    {"category": "Business Ideas", "title": "AI automated newsletter curator", "content": "A tool that scans custom feeds, summarizes key stories using LLMs, and formats HTML newsletters automatically."},
    {"category": "Business Ideas", "title": "Home maintenance local app", "content": "A mobile application matching homeowners with local electricians, plumbers, and gardeners on-demand."},
    {"category": "Business Ideas", "title": "Digital design asset marketplace", "content": "A website where UI designers can sell Figma component libraries and SVG icon packs under subscription."},
    {"category": "Business Ideas", "title": "Building energy tracker", "content": "A hardware-software integration service helping commercial buildings detect energy waste and optimize HVAC usage."},
    {"category": "Business Ideas", "title": "Micro-SaaS invoice generator tool", "content": "A simple API that turns metadata inputs into beautifully formatted PDF invoices for freelancer applications."}
]

def train_and_save():
    print("Initializing TextEmbedding model from fastembed...")
    embed_model = TextEmbedding()
    
    print("Generating embeddings for seed dataset...")
    texts = [f"{item['title']}\n{item['content']}" for item in DATASET]
    embeddings = list(embed_model.embed(texts))
    X = np.array([emb.tolist() for emb in embeddings])
    
    # Label encoding
    label_map = {cat: idx for idx, cat in enumerate(CATEGORIES)}
    y = np.array([label_map[item['category']] for item in DATASET])
    
    print(f"Dataset shape X: {X.shape}, y: {y.shape}")
    
    print("Importing TensorFlow...")
    import tensorflow as tf
    from tensorflow.keras import layers, models
    
    print("Building MLP classifier...")
    model = models.Sequential([
        layers.Input(shape=(384,)),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(32, activation='relu'),
        layers.Dense(len(CATEGORIES), activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("Training model...")
    model.fit(X, y, epochs=35, batch_size=8, verbose=1)
    
    output_dir = os.path.join(os.path.dirname(__file__), "model")
    os.makedirs(output_dir, exist_ok=True)
    
    keras_model_path = os.path.join(output_dir, "classifier.keras")
    model.save(keras_model_path)
    print(f"Model saved to {keras_model_path}")
    
    labels_path = os.path.join(output_dir, "labels.json")
    with open(labels_path, "w") as f:
        json.dump(CATEGORIES, f)
    print(f"Labels saved to {labels_path}")

if __name__ == "__main__":
    train_and_save()
