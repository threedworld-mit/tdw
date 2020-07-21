# Command Deserialization

The build receives [commands](../api/command_api_guide.md) as JSON string and deserializes them into objects. This is an _innately slow process_, albeit highly optimized within TDW.

### Why are commands JSON strings?

JSON is known to be slower than other serialization formats. However, on the backend, JSON allows us to rapidly iterate, fix, and create commands. Switching to a different serialization format would take a tremendous amount of time and result in a faster but much more fragile API; we've decided that this is not a good tradeoff.

### To what extent does deserialization affect performance?

The test controller `do_nothing.py` sends increasing quantities of the command `{"$type": "do_nothing"}` for 1000 iterations. The build responds with an empty frame.

| Quantity | Size (bytes) | FPS |
| --- | --- | --- |
| 1 | 25 | 921 |
| 2 | 50 | 940 |
| 4 | 100 | 919 |
| 8 | 200 | 915 |
| 16 | 400 | 879 |
| 32 | 800 | 825 |
| 64 | 1600 | 780 |
| 128 | 3200 | 676 |
| 256 | 6400 | 578 |
| 512 | 12800 | 408 |
| 1024 | 25600 | 302 |
| 2048 | 51200 | 203 |

### How to run this test

```bash
cd <root>/Python/benchmarking
python3 do_nothing.py
```

```bash
<run build>
```

