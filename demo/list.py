animal=["cat", "dog", "pig"]
print(animal)
print("pig" in animal)
animal.append("eleph")
animal.sort(reverse=True, key=str.lower)
for i in range(0,len(animal)):
    print(animal[i])

print(animal[0:2])
print(animal[0::-1])
print(animal[-2:-1])
print(animal[::2])
print(tuple(animal))

