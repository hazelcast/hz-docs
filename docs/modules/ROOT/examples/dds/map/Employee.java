//tag::emp[]
public class Employee {

    private final String surname;

    public Employee(String surname) {
        this.surname = surname;
    }

    public HazelcastJsonValue toHazelcastJsonValue() {
        return new HazelcastJsonValue("{ \"surname\": \"" + surname + "\" }");
    }
}
//end::emp[]