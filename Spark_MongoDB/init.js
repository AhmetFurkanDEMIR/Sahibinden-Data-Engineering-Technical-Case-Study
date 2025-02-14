db = db.getSiblingDB('sahibinden');

for (let i = 1; i <= 10; i++) {
    db.collection1.insertOne({
        "a": i,
        "b": i * 10,
        "c": [
            { "c1": "x" + i, "c2": i * 100 },
            { "c1": "y" + i, "c2": i * 200 },
            { "c1": "z" + i, "c2": i * 300 }
        ]
    });
}

print("10 tane veri başarıyla eklendi!");
