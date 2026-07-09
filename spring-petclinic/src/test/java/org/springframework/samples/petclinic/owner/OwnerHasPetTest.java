package org.springframework.samples.petclinic.owner;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class OwnerHasPetTest {

	@Test
	void hasPet_returnsTrueForMatchingName_andDoesNotModifyState() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.getPets().add(pet);

		int beforeSize = owner.getPets().size();

		assertTrue(owner.hasPet("Fido"));
		// state unchanged
		assertEquals(beforeSize, owner.getPets().size());
		assertSame(pet, owner.getPets().get(0));
	}

	@Test
	void hasPet_returnsFalseForNonMatchingName() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.getPets().add(pet);

		assertFalse(owner.hasPet("Rex"));
	}

	@Test
	void hasPet_isCaseInsensitive() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.getPets().add(pet);

		assertTrue(owner.hasPet("fIdO"));
	}

	@Test
	void hasPet_returnsFalseForNullArgument() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.getPets().add(pet);

		int beforeSize = owner.getPets().size();

		assertFalse(owner.hasPet(null));
		// state unchanged
		assertEquals(beforeSize, owner.getPets().size());
	}

	@Test
	void hasPet_returnsFalseForEmptyString() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.getPets().add(pet);

		assertFalse(owner.hasPet(""));
	}

}
