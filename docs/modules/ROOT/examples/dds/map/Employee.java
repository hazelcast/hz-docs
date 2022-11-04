//tag::emp[]
public class Employee {

    private final String surname;

    public Employee(String surname) {
        this.surname = surname;
    }

    public static HazelcastJsonValue toHazelcastJsonValue(String surname) {
        return new HazelcastJsonValue("{ \"surname\": \"" + surname + "\" }");
    }
}
//end::emp[]