package org.springframework.samples.petclinic.owner;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class OwnerHasPetTest {

	@Test
	void hasPet_returnsTrue_whenNameMatchesExactly() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.getPets().add(pet);

		int beforeSize = owner.getPets().size();

		assertTrue(owner.hasPet("Fido"));

		// read-only: ensure pets collection wasn't modified
		assertEquals(beforeSize, owner.getPets().size());
		assertEquals("Fido", owner.getPets().get(0).getName());
	}

	@Test
	void hasPet_returnsFalse_whenNoPetMatches() {
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
	void hasPet_returnsFalse_whenNameIsNull() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.getPets().add(pet);

		assertFalse(owner.hasPet(null));
	}

	@Test
	void hasPet_returnsFalse_forEmptyString() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.getPets().add(pet);

		assertFalse(owner.hasPet(""));
	}

}
