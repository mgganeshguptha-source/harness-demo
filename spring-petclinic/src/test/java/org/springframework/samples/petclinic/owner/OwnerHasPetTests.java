package org.springframework.samples.petclinic.owner;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class OwnerHasPetTests {

	@Test
	void should_returnTrueForMatchingName() {
		Owner owner = new Owner();
		Pet p = new Pet();
		p.setName("Fido");
		owner.addPet(p);

		int sizeBefore = owner.getPets().size();
		assertTrue(owner.hasPet("Fido"));
		// read-only: ensure pets collection and pet name unchanged
		assertEquals(sizeBefore, owner.getPets().size());
		assertEquals("Fido", owner.getPets().get(0).getName());
	}

	@Test
	void should_returnFalseForNonMatchingName() {
		Owner owner = new Owner();
		Pet p = new Pet();
		p.setName("Fido");
		owner.addPet(p);

		assertFalse(owner.hasPet("Rover"));
		// ensure collection unchanged
		assertEquals(1, owner.getPets().size());
	}

	@Test
	void should_beCaseInsensitive() {
		Owner owner = new Owner();
		Pet p = new Pet();
		p.setName("Fido");
		owner.addPet(p);

		assertTrue(owner.hasPet("fIdO"));
	}

	@Test
	void should_returnFalseForNullArgument() {
		Owner owner = new Owner();
		Pet p = new Pet();
		p.setName("Fido");
		owner.addPet(p);

		assertFalse(owner.hasPet(null));
	}

	@Test
	void should_returnFalseForEmptyString() {
		Owner owner = new Owner();
		Pet p = new Pet();
		p.setName("Fido");
		owner.addPet(p);

		assertFalse(owner.hasPet(""));
	}

}
