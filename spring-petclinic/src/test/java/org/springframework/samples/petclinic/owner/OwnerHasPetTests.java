package org.springframework.samples.petclinic.owner;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class OwnerHasPetTests {

	@Test
	void hasPet_matchingName_returnsTrue() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.addPet(pet);

		assertTrue(owner.hasPet("Fido"));
	}

	@Test
	void hasPet_nonMatchingName_returnsFalse() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.addPet(pet);

		assertFalse(owner.hasPet("Rex"));
	}

	@Test
	void hasPet_caseInsensitiveMatch_returnsTrue() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.addPet(pet);

		assertTrue(owner.hasPet("fIdO"));
	}

	@Test
	void hasPet_nullArgument_returnsFalse() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.addPet(pet);

		assertFalse(owner.hasPet(null));
	}

	@Test
	void hasPet_emptyString_returnsFalse() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.addPet(pet);

		assertFalse(owner.hasPet(""));
	}

	@Test
	void hasPet_nullPetName_doesNotThrowAndReturnsFalse() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName(null);
		owner.addPet(pet);

		assertFalse(owner.hasPet("Fido"));
	}

	@Test
	void hasPet_noPets_returnsFalse() {
		Owner owner = new Owner();
		// no pets added
		assertFalse(owner.hasPet("Fido"));
	}

	@Test
	void hasPet_whitespaceDoesNotMatch() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName(" Fido ");
		owner.addPet(pet);

		assertFalse(owner.hasPet("Fido"));
	}

	@Test
	void hasPet_doesNotModifyOwnerState() {
		Owner owner = new Owner();
		Pet pet = new Pet();
		pet.setName("Fido");
		owner.addPet(pet);

		int beforeSize = owner.getPets().size();
		boolean result = owner.hasPet("Fido");
		int afterSize = owner.getPets().size();

		assertTrue(result);
		assertEquals(beforeSize, afterSize, "hasPet should not modify pets collection size");
	}

}
