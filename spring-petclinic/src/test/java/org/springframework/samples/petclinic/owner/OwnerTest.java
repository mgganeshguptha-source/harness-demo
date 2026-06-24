package org.springframework.samples.petclinic.owner;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Unit tests for Owner#getFullName()
 */
public class OwnerTest {

	@Test
	void getFullName_returnsFirstAndLastJoinedWithSpace() {
		Owner owner = new Owner();
		owner.setFirstName("John");
		owner.setLastName("Doe");

		String fullName = owner.getFullName();

		assertEquals("John Doe", fullName);
	}

	@Test
	void getFullName_handlesNullFirstName() {
		Owner owner = new Owner();
		owner.setFirstName(null);
		owner.setLastName("Doe");

		String fullName = owner.getFullName();

		assertEquals(" Doe", fullName);
	}

	@Test
	void getFullName_handlesNullLastName() {
		Owner owner = new Owner();
		owner.setFirstName("John");
		owner.setLastName(null);

		String fullName = owner.getFullName();

		assertEquals("John ", fullName);
	}

	@Test
	void getFullName_handlesBothNamesNull() {
		Owner owner = new Owner();
		owner.setFirstName(null);
		owner.setLastName(null);

		String fullName = owner.getFullName();

		assertEquals(" ", fullName);
	}

}
