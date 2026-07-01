package org.springframework.samples.petclinic.owner;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Unit tests for Owner#hasPet(String)
 */
public class OwnerHasPetTest {

	@Test
	void hasPet_returnsTrueWhenNameMatches() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.getPets().add(pet);

		int beforeSize = owner.getPets().size();

		assertTrue(owner.hasPet("Fido"));
		// owner state must not be modified
		assertEquals(beforeSize, owner.getPets().size());
	}

	@Test
	void hasPet_returnsFalseWhenNameDoesNotMatch() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Rex");
		owner.getPets().add(pet);

		int beforeSize = owner.getPets().size();

		assertFalse(owner.hasPet("Fido"));
		assertEquals(beforeSize, owner.getPets().size());
	}

	@Test
	void hasPet_isCaseInsensitive() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("fido");
		owner.getPets().add(pet);

		int beforeSize = owner.getPets().size();

		assertTrue(owner.hasPet("FIDO"));
		assertEquals(beforeSize, owner.getPets().size());
	}

	@Test
	void hasPet_nullArgumentReturnsFalse() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.getPets().add(pet);

		int beforeSize = owner.getPets().size();

		assertFalse(owner.hasPet(null));
		assertEquals(beforeSize, owner.getPets().size());
	}

}
