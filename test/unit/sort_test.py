from eden.sort import Sort


def test_doesnt_sort():
	class Person:
		def __init__(self, name):
			self.name = name

	alice = Person("Alice")
	bob = Person("Bob")
	sort = Sort.default()
	people = [alice, bob]
	sorted_people = sort(people)

	assert sorted_people == [alice, bob]


def test_sorts_ascending_by_attribute():
	class Person:
		def __init__(self, name):
			self.name = name

	alice = Person("Alice")
	bob = Person("Bob")
	sort = Sort.ascending_by("name")
	people = [bob, alice]
	sorted_people = sort(people)

	assert sorted_people == [alice, bob]


def test_sorts_descending_by_attribute():
	class Person:
		def __init__(self, name):
			self.name = name

	alice = Person("Alice")
	bob = Person("Bob")
	sort = Sort.descending_by("name")
	people = [alice, bob]
	sorted_people = sort(people)

	assert sorted_people == [bob, alice]
