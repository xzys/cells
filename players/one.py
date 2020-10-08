print('---')
print(cell.position, cell.velocity)

for found in cell.scan():
    print(found)
    if type(found) is Nutrient:
        cell.set_destination(found.position)
        break
