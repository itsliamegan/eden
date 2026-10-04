from eden.sort import AscendingBy, Default, DescendingBy


def test_doesnt_sort():
	class Person:
		def __init__(self, name):
			self.name = name

	alice = Person("Alice")
	bob = Person("Bob")
	sort = Default()
	people = [alice, bob]
	sorted_people = sort.apply(people)

	assert sorted_people == [alice, bob]


def test_sorts_ascending_by_attribute():
	class Person:
		def __init__(self, name):
			self.name = name

	alice = Person("Alice")
	bob = Person("Bob")
	sort = AscendingBy("name")
	people = [bob, alice]
	sorted_people = sort.apply(people)

	assert sorted_people == [alice, bob]


def test_sorts_descending_by_attribute():
	class Person:
		def __init__(self, name):
			self.name = name

	alice = Person("Alice")
	bob = Person("Bob")
	sort = DescendingBy("name")
	people = [alice, bob]
	sorted_people = sort.apply(people)

	assert sorted_people == [bob, alice]
