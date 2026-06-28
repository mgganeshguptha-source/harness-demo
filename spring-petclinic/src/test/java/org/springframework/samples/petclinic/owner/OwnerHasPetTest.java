package org.springframework.samples.petclinic.owner;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Unit tests for Owner#hasPet(String)
 */
public class OwnerHasPetTest {

	@Test
	void hasPet_returnsTrue_whenNameMatches() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Buddy");
		owner.addPet(pet);

		int beforeSize = owner.getPets().size();
		assertTrue(owner.hasPet("Buddy"));
		// ensure hasPet is read-only
		assertEquals(beforeSize, owner.getPets().size());
	}

	@Test
	void hasPet_returnsFalse_whenNameDoesNotMatch() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Buddy");
		owner.addPet(pet);

		assertFalse(owner.hasPet("Max"));
	}

	@Test
	void hasPet_isCaseInsensitive() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Buddy");
		owner.addPet(pet);

		assertTrue(owner.hasPet("buddy"));
		assertTrue(owner.hasPet("BUDDY"));
	}

	@Test
	void hasPet_returnsFalse_whenNameIsNull() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Buddy");
		owner.addPet(pet);

		assertFalse(owner.hasPet(null));
	}

}
