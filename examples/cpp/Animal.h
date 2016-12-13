/*
 * WARNING! This file was autogenerated.  Do not modify it!
 * 
 * Created using github.com/federicotdn/mabel, version: 0.1.
 * Creation date: 2016-12-13 10:59:34.202070
 * Base: Animal.json
 *
 * Represents an animal with a hat.
 */

#ifndef MODELS_ANIMAL_H
#define MODELS_ANIMAL_H

#include <vector>
#include <string>
#include "Entity.h"
#include "Hat.h"
#include "Color.h"

namespace models {
	struct Animal : public Entity {
		uint32_t m_age;
		float m_height;
		std::vector<Entity> m_friends;
		std::string m_owner = "John";
		bool m_happy = true;
		Color m_color;
		Hat m_hat;
	};
}

#endif //MODELS_ANIMAL_H